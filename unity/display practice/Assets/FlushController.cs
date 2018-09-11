using UnityEngine;
using UnityEngine.UI;

public class FlushController : MonoBehaviour
{
    Image img;
    public float timeout;
    public float timeTrigger;
    public int status;
    public int warm_state;

    void statucheck()
    {
        if (Input.GetKey(KeyCode.W))
        {
            status = 1;
        }
        else if (Input.GetKey(KeyCode.F))
        {
            status = 3;
        }
    }
    

    void timecheck()
    {
        if (Time.time > timeTrigger)
        {
            warm_state *= -1;

            timeTrigger = Time.time + timeout;
        }
    }

    void Start()
    {
        img = GetComponent<Image>();
        img.color = Color.clear;
        status = 0;
        warm_state = 2;
        timeTrigger = 0;
        timeout = 1;
    }

    void Update()
    {
        
        Debug.Log("status "+status);
        Debug.Log("timeTrigger  "+timeTrigger);

        statucheck();

        if (status == 1)
        {
            timecheck();
            if (warm_state == 2)
            {
                this.img.color = Color.Lerp(this.img.color, Color.clear, Time.deltaTime);
            }
            else if (warm_state == -2)
            {
                this.img.color = Color.Lerp(this.img.color, Color.red, Time.deltaTime);
            }
        }
        else if (status == 3)
        {
            this.img.color = new Color(0.5f, 0f, 0f, 0.5f);
        }
    }
}
