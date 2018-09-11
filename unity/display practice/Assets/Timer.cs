using System.Collections;
using UnityEngine.UI;
using UnityEngine;

public class Timer : MonoBehaviour {

    float countTime = 0;

	// Use this for initialization
	void Start () {
		


	}
	
	// Update is called once per frame
	void Update () {
        countTime += Time.deltaTime;
        GetComponent<Text>().text = countTime.ToString("F2");	//少数二桁にして表示
	}
}
